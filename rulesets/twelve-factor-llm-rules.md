# 12-Factor Rules for LLM Software Development

## Core Principles Summary

### I. Codebase
**Rule**: One codebase per app, tracked in Git, deployed to multiple environments
- ✓ Single repository = single app
- ✓ Multiple deploys (dev/staging/prod) from same codebase
- ✗ No code duplication across apps (use libraries instead)

### II. Dependencies
**Rule**: Explicitly declare ALL dependencies with exact versions
- ✓ Use manifest files (package.json, requirements.txt, Gemfile)
- ✓ Use isolation tools (virtualenv, bundler, npm)
- ✗ Never rely on system tools (curl, ImageMagick) - vendor them

### III. Config
**Rule**: Store ALL environment-specific config in environment variables
- ✓ Database URLs, API keys, feature flags → ENV vars
- ✓ Can open-source code without exposing secrets
- ✗ No config files, no grouped "environments", no hardcoded values

### IV. Backing Services
**Rule**: Treat all external services as swappable attached resources
- ✓ Reference via URL/credentials in config
- ✓ Local MySQL = Cloud MySQL = just a config change
- ✗ No distinction between local and third-party services

### V. Build, Release, Run
**Rule**: Strict separation of build → release → run stages
- ✓ Build: compile code + dependencies → artifact
- ✓ Release: build + config → immutable release with ID
- ✓ Run: execute release (keep minimal for reliability)

### VI. Processes
**Rule**: Run app as stateless, share-nothing processes
- ✓ Store persistent data in backing services only
- ✓ File system = temporary scratch space only
- ✗ No sticky sessions, no in-memory state between requests

### VII. Port Binding
**Rule**: Self-contained apps export services via port binding
- ✓ App includes web server library (Express, Puma, Jetty)
- ✓ Binds to PORT env var, serves HTTP independently
- ✗ No runtime webserver injection (Apache modules, WAR files)

### VIII. Concurrency
**Rule**: Scale horizontally via process model
- ✓ Different process types for different workloads (web, worker)
- ✓ Scale by adding more processes, not threads
- ✓ Let process manager handle lifecycle

### IX. Disposability
**Rule**: Processes start fast (<5s) and shutdown gracefully
- ✓ Handle SIGTERM → finish current work → exit
- ✓ Design for sudden death (return jobs to queue)
- ✗ No long startup/shutdown procedures

### X. Dev/Prod Parity
**Rule**: Keep all environments as identical as possible
- ✓ Same backing services everywhere (PostgreSQL in dev AND prod)
- ✓ Deploy continuously (hours, not weeks)
- ✓ Developers deploy their own code

### XI. Logs
**Rule**: Write logs as unbuffered event streams to stdout
- ✓ One event per line to stdout
- ✓ Let execution environment handle routing/storage
- ✗ No log files, no custom log routing in app

### XII. Admin Processes
**Rule**: Run admin tasks as identical one-off processes
- ✓ Same codebase, same config, same dependencies
- ✓ Run via: `heroku run rails console` or `kubectl exec`
- ✗ No separate admin apps or special environments

## LLM Implementation Context

### For Creating New Applications

When implementing a new application, the LLM should:

1. **Project Structure**
   ```
   myapp/
   ├── src/           # Application code
   ├── config/        # App configuration (NOT env-specific)
   ├── package.json   # Dependencies (explicit versions)
   ├── .env.example   # Document required ENV vars
   ├── Dockerfile     # Self-contained runtime
   └── README.md      # Setup and deployment instructions
   ```

2. **Code Patterns**
   ```javascript
   // Good: Config from environment
   const db = new Database({
     url: process.env.DATABASE_URL,
     poolSize: parseInt(process.env.DB_POOL_SIZE || '5')
   });

   // Bad: Hardcoded or file-based config
   const db = new Database({
     host: 'localhost',
     password: config.production.password
   });
   ```

3. **Dependency Declaration**
   ```json
   // package.json - explicit versions
   {
     "dependencies": {
       "express": "4.18.2",
       "pg": "8.11.3",
       "redis": "4.6.5"
     }
   }
   ```

4. **Process Management**
   ```javascript
   // Graceful shutdown
   process.on('SIGTERM', async () => {
     console.log('SIGTERM received, closing HTTP server');
     server.close(() => {
       console.log('HTTP server closed');
       process.exit(0);
     });
   });
   ```

### For Checking Existing Applications

When validating 12-factor compliance, check:

1. **Codebase Violations**
   - Multiple apps in one repo?
   - Shared code not extracted to libraries?
   - Missing version control?

2. **Dependency Violations**
   - Missing dependency manifest?
   - Relying on system packages?
   - No dependency isolation?

3. **Config Violations**
   - Hardcoded values in code?
   - Environment-specific files committed?
   - Config not in ENV vars?

4. **State Violations**
   - Storing user sessions in memory?
   - Using local filesystem for permanent storage?
   - Assuming process persistence?

5. **Port Binding Violations**
   - Requires external web server?
   - Not self-contained?
   - No PORT configuration?

### Quick Validation Checklist

```bash
# Can I...
- Clone and run with just runtime + deps? ✓
- Deploy to new environment by changing ENV vars only? ✓
- Scale by running more processes? ✓
- Kill any process without data loss? ✓
- See all logs in stdout? ✓
- Run admin commands with same build? ✓

# Do I have...
- Hardcoded config? ✗
- Local file storage? ✗
- In-memory session state? ✗
- Special "environments"? ✗
- Startup scripts? ✗
```

### Common Anti-Patterns to Avoid

1. **Config Anti-Pattern**: `config/environments/production.rb`
   → Use: `process.env.RAILS_ENV` + individual ENV vars

2. **State Anti-Pattern**: In-memory caching between requests
   → Use: Redis/Memcached backing service

3. **Dependency Anti-Pattern**: `apt-get install imagemagick` in docs
   → Use: Include binary or use service API

4. **Logging Anti-Pattern**: `winston.createLogger({filename: 'app.log'})`
   → Use: `console.log()` to stdout

5. **Process Anti-Pattern**: `pm2 start app.js --daemon`
   → Use: Let platform manage processes

### Implementation Priority

When implementing or refactoring:
1. **First**: Fix config (Factor III) - enables deployment flexibility
2. **Second**: Fix dependencies (Factor II) - enables reproducible builds
3. **Third**: Fix backing services (Factor IV) - enables service swapping
4. **Fourth**: Fix processes (Factor VI) - enables horizontal scaling
5. **Last**: Optimize startup/shutdown (Factor IX) - improves operations

This framework allows an LLM to both generate compliant code and audit existing applications for 12-factor adherence.