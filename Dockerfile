FROM marcbperez/docker-gradle
MAINTAINER marcbperez@users.noreply.github.com

ADD . /home/builder
WORKDIR /home/builder
ENV FLASK_APP="restfuloauth2"
ENV SECRET_KEY="non-production-key"
CMD gradle --continuous
