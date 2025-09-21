FROM busybox:latest

# Cria diretório onde o httpd do busybox vai servir
WORKDIR /www

COPY . /www

# Expor a porta que vamos usar (3000)
EXPOSE 3000

# Inicia o httpd do busybox em foreground na porta 3000
CMD ["httpd", "-f", "-p", "3000"]
