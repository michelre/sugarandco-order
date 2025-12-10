SERVER_USER=ubuntu
SERVER_HOST=217.182.168.186
APP_DIR=/var/www/sugarandco-order

SSH = ssh $(SERVER_USER)@$(SERVER_HOST)
RSYNC = rsync -avz --delete --progress \
	--exclude 'venv' \
	--exclude 'Makefile.server' \
	--exclude 'db.sqlite3' \
	--exclude '.git' \
	--exclude '__pycache__' \
	--exclude '.pytest_cache' \
	--exclude '*.pyc' \
	--exclude '.env' \
	--exclude 'orderapp/settings.py' \
	-e "ssh"

deploy:
	$(RSYNC) ./ $(SERVER_USER)@$(SERVER_HOST):$(APP_DIR)/
	$(SSH) "cd $(APP_DIR) && make -f Makefile.server server-setup"