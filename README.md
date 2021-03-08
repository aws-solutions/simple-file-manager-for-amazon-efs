# Running the web app locally


1. Clone Repo
2. cd into the source/web/ directory
3. npm install (only need to do this the first time or when the package.json is updated)
4. npm run serve (this will spin up a local hot-reloading webserver)

Notes: 

You will need to adjust the api URL in two places:

1. The file named runtimeConfig.json (source/web/public/)
2. Inside the upload component within the dropzone settings object (source/web/src/components/upload.vue)


# Deploying the API

1. Make sure your aws cli is setup and working correctly
2. Make sure you have python3 installed
3. Create a "root" all access AWS IAM role for your account (this will change once I finish the auth work)
4. Configure the chlalice config.json to use the role

        source/api/.chalice/config.json
        
        iam_role_arn": "your_role_arn_here"
        
5. cd into the `source/deployment` directory
6. Run the build script
    
    `./build-s3-dist.sh --template-bucket efs-build-test-us-west-2 --code-bucket efs-build-test --region us-west-2 --version v0.0.7`

7. Deploy the cloudformation template return from the output of the script