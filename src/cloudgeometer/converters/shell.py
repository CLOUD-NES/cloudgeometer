import shlex
import subprocess
from typing import Any

from .base import ConversionResult


class ShellMixin:
    """Mixin for converters that delegate to external CLI tools.

    Handles templating, execution, and capturing output.
    """

    def run_command(
        self,
        template: str,
        context: dict[str, Any],
        env: dict[str, str] | None = None,
        cwd: str | None = None,
        timeout: int = 3600,
    ) -> tuple[int, str, str]:
        """Render a command template and run it.

        Template example:
            `gdal_translate -of COG -co COMPRESS={compression} -co BLOCKSIZE={blocksize} {src} {dst}`

        Returns:
            tuple[int, str, str]: returncode, stdout, stderr.
        """
        cmd = template.format(**context)
        result = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            env=env,
            cwd=cwd,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr

    def _shell_result(
        self,
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> ConversionResult:
        return ConversionResult(
            success=(returncode == 0),
            stdout=stdout,
            stderr=stderr,
        )
