pipeline { 
    agent any;
    stages {
        stage("Code") {
            steps {
                git url: 'https://github.com/raeelhaider/flask-app.git',branch:'main' 
            }
        }
        stage("Build") {
            steps {
                sh 'docker build -t flask-app .' //In order to use this built in a runtime and to get the latest image each time we have used image : . build in dockerfile so we can get an updated code each time.
            }
        }    
        stage("Test") {
            steps {
                echo "Done"
            }
        }
                stage("Push to Docker Hub") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId:'dockerHubCreds',
                    usernameVariable:'dockerHubUser',
                    passwordVariable:'dockerHubPass')]){
                        sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                        sh "docker image tag flask-app ${env.dockerHubUser}/flask-app:latest"
                        sh "docker push ${env.dockerHubUser}/flask-app:latest"
                    }
            }
        }
        stage("Deployment") {
            steps {
                sh "docker compose down"
                sh "docker compose up --build -d"
            }
        }
  }
} 
