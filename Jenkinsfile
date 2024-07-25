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
	    AGB_VERSION = sh(returnStdout: true, script: "cat alphagamebot.json | jq '.VERSION' -cMr").trim()
	    COMMIT_MESSAGE = sh(script: 'git log -1 --pretty=%B ${GIT_COMMIT}', returnStdout: true).trim()

        // MySQL stuff
        MYSQL_HOST = "hubby.internal"
        MYSQL_DATABASE = "alphagamebot"
        MYSQL_USER = "alphagamebot" 
        MYSQL_PASSWORD = credentials('alphagamebot-mysql-password')

        REDDIT_API_SECRET = credentials('alphagamebot-reddit-secret')
        REDDIT_API_ID = "q2WqT5ZGLhdiyjKZO0P9Og"
    }
    stages {
        stage('build') {
            steps {
                // debug if necessary
                // sh 'printenv'

                echo "Building"
                sh 'docker build -t alphagamedev/alphagamebot:$AGB_VERSION \
                                --build-arg COMMIT_MESSAGE="$COMMIT_MESSAGE" \
                                --build-arg BUILD_NUMBER=$BUILD_NUMBER \
                                --build-arg BRANCH_NAME=$BRANCH_NAME .'

            }
        }
        stage('push') {
            when { 
                // We ONLY want to push Docker images when we are in the master branch!
                branch 'master'
            }
            steps {
                echo "Pushing image to Docker Hub"
                sh 'echo $DOCKER_TOKEN | docker login -u alphagamedev --password-stdin'
                sh 'docker tag  alphagamedev/alphagamebot:$AGB_VERSION alphagamedev/alphagamebot:latest' // point tag latest to most recent version
                sh 'docker push alphagamedev/alphagamebot:$AGB_VERSION' // push tag latest version
                sh 'docker push alphagamedev/alphagamebot:latest' // push tag latest
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
                                -e TOKEN -e WEBHOOK -e BUILD_NUMBER \
                                -e MYSQL_HOST -e MYSQL_DATABASE -e MYSQL_USER -e MYSQL_PASSWORD \
                                -e REDDIT_API_SECRET -e REDDIT_API_ID --restart=always --net=host \
                                alphagamedev/alphagamebot:$AGB_VERSION -rs" // add alphagamebot flags
            }
        }
    } // stages
}
