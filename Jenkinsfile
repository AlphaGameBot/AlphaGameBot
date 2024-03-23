pipeline {
    agent {
        docker {
            image 'boisvert/scala-build'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }
    environment {
        TOKEN = credentials('alphagamebot-token')
    }
    stages {
        stage('build') {
            steps {
                // debug if necessary
                // sh 'printenv'

                echo "Building"

                sh 'docker build -t alphagamedev/alphagamebot .'

            }
        }
        stage('deploy') {
            steps {
                // conditionally deploy
                sh "docker container stop alphagamebot || true"
                sh "docker container rm alphagamebot || true"
                sh "docker run -d -v /mnt/bigga/alphagamebot-cache.sqlite:/docker/request-handler.sqlite --name alphagamebot -e TOKEN=$TOKEN --restart=always alphagamedev/alphagamebot"
            }
        }
    }
}