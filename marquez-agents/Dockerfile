# 使用Python 3.13官方镜像
FROM python:3.13-slim

# 设置环境变量和工作目录
ENV PYTHONPATH=/app/src \
    ENV_FOR_DYNACONF=development \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 一次性安装系统依赖和创建用户
RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev curl \
    && useradd -m -u 1000 appuser \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装Python依赖
COPY pyproject.toml README.md ./
RUN pip install -e . && rm -rf /root/.cache/pip

# 复制应用代码并设置权限
COPY src/ ./src/
COPY config/ ./config/
COPY run_streamlit.py ./
RUN chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8504

# 健康检查 - 检查Streamlit端口是否可访问
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8504/ || exit 1

# 启动命令
CMD ["python", "run_streamlit.py"]
