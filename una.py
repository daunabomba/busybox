import subprocess
import os
import multiprocessing
from pathlib import Path
from mods.utils import get_cross_prefix
from mods.build import SubprocessRunner
from mods import colors
from mods.build import get_build_env


# Module-level runner, initialized when needed
_runner = None

def _get_runner(trace_file=None):
    """Get or create the subprocess runner."""
    global _runner
    if _runner is None:
        _runner = SubprocessRunner(trace_file)
    return _runner

def set_trace_file(trace_file):
    """Set the trace file for subprocess logging."""
    global _runner
    _runner = SubprocessRunner(trace_file)

def target_configure(staging_dir: Path, image_dir: Path, arch="x32"):
    colors.info(f"Busybox: target_configure (defconfig) for {arch}")
    repo_root = Path(__file__).parent
    
    cross = get_cross_prefix(arch)
    std_flags = os.environ.get("CFLAGS", "")
    static_flags = os.environ.get("CFLAGS_STATIC", "")
    
    cmd = [
        "make",
        "V=1",
        f"CROSS_COMPILE={cross}",
        "HOSTCC=clang",
        "CC=clang",
        "AR=llvm-ar",
        "NM=llvm-nm",
        "LD=ld.lld",
        "STRIP=llvm-strip",
        f"CFLAGS={std_flags}",
        f"CFLAGS_busybox={static_flags}",
        "defconfig"
    ]
    _get_runner().run(cmd, cwd=repo_root, env=get_build_env(), check=True)
    
    # Disable CONFIG_STATIC_LIBGCC as we use Clang/LLVM runtimes
    colors.info(f"Busybox: disabling CONFIG_STATIC_LIBGCC")
    config_path = repo_root / ".config"
    if config_path.exists():
        content = config_path.read_text()
        content = content.replace("CONFIG_STATIC_LIBGCC=y", "# CONFIG_STATIC_LIBGCC is not set")
        # Disable hardware acceleration options
        hwaccel_options = [
            "CONFIG_SHA1_HWACCEL",
            "CONFIG_SHA256_HWACCEL", 
        ]
        for option in hwaccel_options:
            content = content.replace(f"{option}=y", f"# {option} is not set")

        config_path.write_text(content)

def target_build(staging_dir: Path, image_dir: Path, arch="x32"):
    colors.info(f"Busybox: target_build ({arch})")
    repo_root = Path(__file__).parent
    make_jobs = multiprocessing.cpu_count()
    
    cross = get_cross_prefix(arch)
    std_flags = os.environ.get("CFLAGS", "")
    static_flags = os.environ.get("CFLAGS_STATIC", "")
    
    cmd = [
        "make",
        "V=1",
        f"CROSS_COMPILE={cross}",
        "HOSTCC=clang",
        "CC=clang",
        "AR=llvm-ar",
        "NM=llvm-nm",
        "LD=ld.lld",
        "STRIP=llvm-strip",
        f"CFLAGS={std_flags}",
        f"CFLAGS_busybox={static_flags}",
        f"-j{make_jobs}"
    ]
    _get_runner().run(cmd, cwd=repo_root, env=get_build_env(), check=True)

def target_install(staging_dir: Path, image_dir: Path, arch="x32"):
    colors.info(f"Busybox: target_install ({arch})")
    repo_root = Path(__file__).parent
    make_jobs = multiprocessing.cpu_count()
    
    cross = get_cross_prefix(arch)
    std_flags = os.environ.get("CFLAGS", "")
    static_flags = os.environ.get("CFLAGS_STATIC", "")
    
    cmd = [
        "make",
        "V=1",
        f"CONFIG_PREFIX={image_dir}",
        f"CROSS_COMPILE={cross}",
        "HOSTCC=clang",
        "CC=clang",
        "AR=llvm-ar",
        "NM=llvm-nm",
        "LD=ld.lld",
        "STRIP=llvm-strip",
        f"CFLAGS={std_flags} -O2",
        f"CFLAGS_busybox={static_flags}",
        "install",
        f"-j{make_jobs}"
    ]
    _get_runner().run(cmd, cwd=repo_root, env=get_build_env(), check=True)
