import subprocess
import os
import multiprocessing
from pathlib import Path
from mods.utils import get_cross_prefix
from mods import colors

def get_env():
    env = os.environ.copy()
    host_bin = Path(__file__).parent.parent.parent / "bld" / "host" / "bin"
    env["PATH"] = f"{host_bin}:{env.get('PATH', '')}"
    return env

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
    subprocess.run(cmd, cwd=repo_root, env=get_env(), check=True)
    
    # Disable CONFIG_STATIC_LIBGCC as we use Clang/LLVM runtimes
    colors.info(f"Busybox: disabling CONFIG_STATIC_LIBGCC")
    config_path = repo_root / ".config"
    if config_path.exists():
        content = config_path.read_text()
        content = content.replace("CONFIG_STATIC_LIBGCC=y", "# CONFIG_STATIC_LIBGCC is not set")
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
    subprocess.run(cmd, cwd=repo_root, env=get_env(), check=True)

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
    subprocess.run(cmd, cwd=repo_root, env=get_env(), check=True)
