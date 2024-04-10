FROM nginx:1.25

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

COPY zerossl_certificate.crt /crt/
COPY private.key /crt/