docker run -p 5000:80 \
  --env slid_token="" \
  --rm --name=starline -v $PWD:/app starline:dev
