#!/usr/bin/env python3
"""
GitHub Copilot CLI Agent Runner
This script runs GitHub Copilot CLI agent on dataset entries
"""

import subprocess
import sys
import shutil
from pathlib import Path
import logging
import json
import os

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Configuration-related errors."""


class AgentError(Exception):
    """Custom exception for agent errors"""
    pass


__all__ = ["Config", "get_config"]


def _get_git_root() -> Path:
    """Get the git root directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        # Fallback to file-based resolution if not in a git repo
        return Path(__file__).parent.parent.parent


class PathConfig:
    """File and directory paths."""

    root: Path

    @classmethod
    def from_root(cls, root: Path):
        """Create path configuration from repository root."""
        return cls(
            root=root
        )


class TimeoutConfig:
    """Timeout configuration for various operations."""

    build_baseapp: int
    build_app: int
    test_execution: int
    github_copilot_cli: int

    @classmethod
    def default(cls) :
        """Get default timeout configuration."""
        return cls(
            build_baseapp=30 * 60,  # 30 minutes for BaseApp compilation
            build_app=5 * 60,  # 5 minutes for application compilation
            test_execution=3 * 60,  # 3 minutes for test execution
            github_copilot_cli=30 * 60,  # 30 minutes for GitHub Copilot CLI execution
        )


class FilePatternConfig:
    """File patterns and naming conventions."""

    trajectory_pattern: str
    patch_pattern: str
    instance_pattern: str
    result_pattern: str
    copilot_instruction_naming: str
    copilot_instructions_dirname: str
    copilot_instructions_pattern: str

    @classmethod
    def default(cls, instance_pattern: str):
        """Get default file pattern configuration."""
        return cls(
            trajectory_pattern=".traj.json",
            patch_pattern=".patch",
            instance_pattern=instance_pattern,
            result_pattern=".jsonl",
            copilot_instruction_naming="copilot-instructions.md",
            copilot_instructions_dirname="instructions",
            copilot_instructions_pattern="*.instructions.md",
        )


class EnvironmentConfig:
    """Environment-specific configuration."""

    # Azure DevOps
    ado_token: str | None

    # GitHub Actions
    github_output: str | None
    github_step_summary: str | None
    github_actions: bool
    runner_debug: bool

    @classmethod
    def from_environment(cls):
        """Load configuration from environment variables."""
        return cls(
            ado_token=os.getenv("ADO_TOKEN"),
            github_output=os.getenv("GITHUB_OUTPUT"),
            github_step_summary=os.getenv("GITHUB_STEP_SUMMARY"),
            github_actions=os.getenv("GITHUB_ACTIONS") == "true",
            runner_debug=os.getenv("RUNNER_DEBUG") == "1",
        )


class Config:
    """Centralized configuration for BC-Bench."""

    paths: PathConfig
    env: EnvironmentConfig
    timeout: TimeoutConfig
    file_patterns: FilePatternConfig

    @classmethod
    def load(cls) :
        root = _get_git_root()
        path_config = PathConfig.from_root(root)

        with open(path_config.dataset_schema_path) as f:
            schema = json.load(f)

        instance_pattern = schema.get("properties", {}).get("instance_id", {}).get("pattern")

        return cls(
            paths=path_config,
            env=EnvironmentConfig.from_environment(),
            timeout=TimeoutConfig.default(),
            file_patterns=FilePatternConfig.default(instance_pattern),
        )

    def resolve_ado_token(self) -> str:
        if not self.env.ado_token:
            raise ConfigurationError("ADO_TOKEN environment variable is required")
        return self.env.ado_token



# Singleton instance
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config  # noqa: PLW0603
    if _config is None:
        load_dotenv()
        _config = Config.load()
    return _config

def run_copilot_agent(repo_path: Path):
    """Run GitHub Copilot CLI agent.

    Returns:
        Dictionary containing metrics extracted from the CLI output, or None if collection fails
        Boolean indicating if execution was successful
    """
    logger.info(f"Running GitHub Copilot CLI")
    logger.info(f"Executing Copilot CLI in directory: {repo_path}")
    #logger.debug(f"Using prompt:\n{prompt}")

    copilot_cmd = shutil.which("copilot")
    if not copilot_cmd:
        raise AgentError("Copilot CLI not found in PATH. Please ensure it is installed and available.")

    try:
        cmd_args = [
            copilot_cmd,
            "--allow-all-tools",
            "--allow-all-paths",
            "--disable-builtin-mcps",
            f"--model=claude-haiku-4.5",
            "--log-level=debug",
            f"--prompt= What is the meaning and structure of this repository? After you reply, use gh to make a hello world on the last PR",
            "--no-custom-instructions"
        ]

        #logger.debug(f"Copilot command args: {cmd_args}")

        #repo_path = _config.paths.root

        # Ensure GH_PAT is passed to subprocess
        env = os.environ.copy()
        if not env.get("GH_TOKEN"):
            logger.warning("GH_TOKEN not found in environment")
        
        result = subprocess.run(
            cmd_args,
            cwd=str(repo_path),
            stderr=subprocess.PIPE,
            timeout=300,
            check=True,
            env=env,
        )

        if result.stderr:
            sys.stdout.buffer.write(result.stderr)
            sys.stdout.buffer.flush()
        logger.info(f"Copilot CLI run complete")

        stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
        return parse_metrics(stderr.splitlines()), True
    except subprocess.TimeoutExpired:
        logger.error(f"Copilot CLI timed out after 300 seconds")
        return None, False
    except subprocess.CalledProcessError as e:
        logger.error(f"Copilot CLI execution failed with error {e.stderr}")
        raise AgentError(f"Copilot CLI execution failed: {e}") from None
    except Exception as e:
        logger.exception(f"Unexpected error running Copilot CLI: {e}")
        raise


def parse_metrics(stderr_lines: list[str]) -> dict[str, float | int] | None:
    """Parse metrics from stderr output"""
    metrics = {}
    for line in stderr_lines:
        if "tokens" in line.lower() or "cost" in line.lower():
            logger.info(f"Metric: {line}")
    return metrics if metrics else None


def main():
    """Main function to run Copilot CLI agent"""
    
    logger.info("=== GitHub Copilot CLI Agent Runner ===")
    
    # Setup paths
    repo_path = Path.cwd()
    output_dir = repo_path / "copilot_logs"
    output_dir.mkdir(exist_ok=True)
    
    # Configuration
    model = "gpt-4"
    prompt = "Analyze this repository and provide a summary of its structure and purpose"
    
    try:
        metrics, success = run_copilot_agent(repo_path)
        
        if success:
            logger.info("✓ Copilot CLI execution completed successfully")
            if metrics:
                logger.info(f"Metrics collected: {metrics}")
        else:
            logger.warning("⚠ Copilot CLI execution completed with warnings")
            
    except AgentError as e:
        logger.error(f"✗ Agent error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"✗ Unexpected error: {e}")
        sys.exit(1)
    
    logger.info("=== Script completed ===")


if __name__ == "__main__":
    main()