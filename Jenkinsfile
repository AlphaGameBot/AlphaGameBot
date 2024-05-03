pipeline {
    agent {
        docker {
            image 'boisvert/python-build'
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
                sh """
                    # Retrieve the AGB_VERSION from the JSON file
                    export AGB_VERSION=\$(cat alphagamebot.json | jq '.VERSION' -c -M -r)

                    # Check if AGB_VERSION is empty, and if so, assign a fallback value
                    if [ -z "\$AGB_VERSION" ]; then
                        AGB_VERSION='latest'
                    fi


                """
                sh 'echo "AGB_VERSION is: \$AGB_VERSION"'
                sh 'docker build -t alphagamedev/alphagamebot:$AGB_VERSION .'

                // get alphagamebot version


            }
        }
        stage('push') {
            steps {
                echo "Pushing image to Docker Hub"
                sh 'echo $DOCKER_TOKEN | sudo docker login -u alphagamedev --password-stdin'
                sh 'docker push alphagamedev/alphagamebot:\$AGB_VERSION'
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
