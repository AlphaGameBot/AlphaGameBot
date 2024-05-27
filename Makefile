clean:
	docker container rm alphagamebot -f || true
	docker container rm alphagamebot_test -f || true
	
build:
	docker build -t alphagamedev/alphagamebot:dev .
run: clean
	docker build -t alphagamedev/alphagamebot:dev .
	docker run --rm -it --name alphagamebot --env-file .env alphagamedev/alphagamebot:dev

small: clean
	docker run --rm -it --name alphagamebot --env-file .env -v /home/damien/AlphaGameBot/:/docker/ alphagamedev/alphagamebot:dev

test:
	docker run --rm -it --name alphagamebot_test alphagamedev/alphagamebot:dev python3 /docker/run_tests.py