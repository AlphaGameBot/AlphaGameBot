pipeline {
    agent {
        docker {
            image 'boisvert/scala-build'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }
    environment {
        TOKEN = credentials('alphagamebot-token')
	    WEBHOOK = credentials('alphagamebot-webhook')
	    DOCKER_TOKEN = credentials('alphagamedev-docker-token')
    }
    stages {
        stage('build') {
            steps {
                // debug if necessary
                // sh 'printenv'

                echo "Building"
                sh "AGB_VERSION=\$(cat alphagamebot.json | jq '.VERSION' -c -M -r)"
                sh 'docker build -t alphagamedev/alphagamebot:$AGB_VERSION .'

                // get alphagamebot version


            }
        }
        stage('push') {
            steps {
                echo "Pushing image to Docker Hub"
                sh 'echo $DOCKER_TOKEN | sudo docker login -u alphagamedev --password-stdin'
                sh 'docker push alphagamedev/alphagamebot:$AGB_VERSION'
                sh 'docker logout'
            }
        }
        stage('deploy') {
            steps {
                // conditionally deploy
                sh "docker container stop alphagamebot || true"
                sh "docker container rm alphagamebot || true"
                sh "docker run -d -v /mnt/bigga/alphagamebot-cache.sqlite:/docker/request-handler.sqlite --name alphagamebot -e TOKEN -e WEBHOOK --restart=always alphagamedev/alphagamebot"
            }
        }
    } // stages
}
