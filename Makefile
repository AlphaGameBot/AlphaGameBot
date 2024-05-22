clean:
	docker container rm alphagamebot -f || true

run: clean
	docker build -t alphagamedev/alphagamebot:dev .
	docker run --rm -it --name alphagamebot --env-file .env alphagamedev/alphagamebot:dev

test: clean
	docker run --rm -it --name alphagamebot --env-file .env -v /home/damien/AlphaGameBot/:/docker/ alphagamedev/alphagamebot:dev
