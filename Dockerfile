FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

#RUN apt-get update

RUN curl --location  http://vina.scripps.edu/download/autodock_vina_1_1_2_linux_x86.tgz > autodock_vina.tar.gz && \
tar -vxzf autodock_vina.tar.gz && \ 
mv autodock_vina_1_1_2_linux_x86 /usr/local/bin/ && \
rm autodock_vina.tar.gz

ENV PATH="${PATH}:/usr/local/bin/autodock_vina_1_1_2_linux_x86/bin" 
 
# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
