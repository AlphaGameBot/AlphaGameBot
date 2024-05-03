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
	    AGB_VERSION = sh(returnStdout: true, script: "cat alphagamebot.json | jq '.VERSION' -c -M -r").trim()
	    COMMIT_MESSAGE = sh(script: 'git log -1 --pretty=%B ${GIT_COMMIT}', returnStdout: true).trim()
    }
    stages {
        stage('build') {
            steps {
                // debug if necessary
                // sh 'printenv'

                echo "Building"
                sh 'docker build -t alphagamedev/alphagamebot:$AGB_VERSION .'

                // get alphagamebot version


            }
        }
        stage('push') {
            steps {
                echo "Pushing image to Docker Hub"
                sh 'echo $DOCKER_TOKEN | docker login -u alphagamedev --password-stdin'
                sh 'docker push alphagamedev/alphagamebot:$AGB_VERSION'
                sh 'docker logout'
            }
        }
        stage('deploy') {
            steps {
                // conditionally deploy
                sh "docker container stop alphagamebot || true"
                sh "docker container rm alphagamebot || true"
                sh "docker run -d \
                                -v /mnt/bigga/alphagamebot-cache.sqlite:/docker/request-handler.sqlite \
                                --name alphagamebot \
                                -e TOKEN -e WEBHOOK -e BUILD_NUMBER -e BRANCH_NAME \
                                -e BRANCH_IS_PRIMARY -e BUILD_ID -e BUILD_TAG -e COMMIT_MESSAGE \
                                --restart=always \
                                alphagamedev/alphagamebot:$AGB_VERSION"
            }
        }
    } // stages
}
