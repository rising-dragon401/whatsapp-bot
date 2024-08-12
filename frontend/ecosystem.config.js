module.exports = {
    apps: [
      {
        name: 'wabot-frontend',
        script: 'node_modules/.bin/next',
        args: 'start',
        cwd: './', // Path to your project directory
        exec_mode: 'cluster', // Enable cluster mode for load balancing
        instances: 'max', // Number of instances based on the number of CPUs
        autorestart: true, // Automatically restart on crashes
        watch: false, // Disable file watching (set to true for development)
        env: {
          NODE_ENV: 'production'
        }
      }
    ]
  };
  