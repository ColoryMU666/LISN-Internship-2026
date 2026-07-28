FROM alpine:latest

RUN apk add bash ttyd uv python3 vim git

# Enable file transfers from the shell through the browser with tsz / trz
# Caveat: this is not supported / accepted by default by all browsers
# Caveat: the tool is installed in /root/.local rather than system wide; hence not accessible if that directory is hidden by a mounted file system 
RUN uv init /opt/venv && cd /opt/venv && uv --cache-dir .cache add --python /usr/bin/python trzsz-svr && uv cache clean

ENV PATH /opt/venv/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV UV_LINK_MODE=symlink
ENV UV_NO_SYNC=1
ENV UV_CACHE_DIR=/shared/uv

RUN mkdir app/
# remove message on initial login
#RUN echo "" >/etc/motd

#ENTRYPOINT [""]

EXPOSE 8888