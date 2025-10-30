# Deployment Guide

This guide covers deploying Object Detection API to both GitHub and Render.

## Part 1: Deploy to GitHub

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in the details:
   - **Repository name**: `ObjectDetection_ML_Deployment`
   - **Description**: "Real-time object detection API with FastAPI, YOLOv8, and Docker"
   - **Visibility**: Public (for portfolio) or Private
   - ⚠️ **DO NOT** initialize with README, .gitignore, or license (we already have these)

3. Click **"Create repository"**

### Step 2: Push to GitHub

Copy and run these commands in your terminal:

```bash
# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ObjectDetection_ML_Deployment.git

# Push all commits
git push -u origin main
```

If you get an authentication error, GitHub now requires Personal Access Tokens:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "Deployment Token"
4. Select scope: `repo` (full control of private repositories)
5. Click "Generate token"
6. Copy the token (you won't see it again!)
7. Use the token as your password when pushing

### Step 3: Verify

Visit your GitHub repository URL:
```
https://github.com/YOUR_USERNAME/ObjectDetection_ML_Deployment
```

You should see:
- ✅ All your code
- ✅ README with project description
- ✅ 3 commits
- ✅ Dockerfile and docker-compose.yml
- ✅ Documentation files

---

## Part 2: Deploy to Render

### Prerequisites

1. Create a free Render account: https://render.com/
2. Sign up with GitHub (recommended) or email
3. Verify your email

### Step 1: Connect GitHub to Render

1. Log in to Render Dashboard: https://dashboard.render.com/
2. Click **"New +"** → **"Blueprint"**
3. Click **"Connect GitHub"**
4. Authorize Render to access your GitHub account
5. Select **"All repositories"** or **"Only select repositories"**
6. Choose your `ObjectDetection_ML_Deployment` repository

### Step 2: Deploy Using Blueprint

1. Render will detect the `render.yaml` file
2. You'll see a preview of the deployment
3. Click **"Apply"**
4. Render will:
   - ✅ Create a new web service
   - ✅ Build the Docker image (~5-10 minutes first time)
   - ✅ Deploy the container
   - ✅ Assign a public URL

### Step 3: Monitor Deployment

Watch the build logs in real-time:
- You'll see Docker building the image
- Installing dependencies
- Downloading the YOLO model
- Starting the server

**Expected build time**: 8-12 minutes (first deployment)

### Step 4: Get Your Live URL

Once deployment succeeds, you'll get a URL like:
```
https://object-detection-api-xxxx.onrender.com
```

**Test it:**
- Demo UI: https://your-app.onrender.com/
- API Docs: https://your-app.onrender.com/docs
- Health Check: https://your-app.onrender.com/health

---

## Understanding Render Free Tier

### ⚠️ Important: Cold Starts

**What happens:**
- After **15 minutes of inactivity**, your app goes to sleep
- First request after sleep takes **30-60 seconds** to wake up
- Subsequent requests are fast

**Why this happens:**
- Free tier limitation
- Render shuts down idle apps to save resources

**Solutions:**
1. **Accept it**: Fine for demos and portfolio
2. **Keep-alive service**: Ping your app every 10 minutes (external service)
3. **Upgrade**: $7/month for always-on service

### Resource Limits

Free tier includes:
- ✅ 750 hours/month
- ✅ 512MB RAM
- ✅ 0.1 CPU (shared)
- ✅ Automatic HTTPS
- ✅ Custom domains (paid plans)

**Is this enough?**
- ✅ Yes for demos/portfolio
- ✅ Yes for light usage (< 100 requests/day)
- ⚠️ May struggle with simultaneous requests
- ⚠️ Large images (>5MB) may timeout

---

## Troubleshooting

### Build Fails: "Out of Memory"

**Symptom:** Build crashes during PyTorch installation

**Solution:** This is rare with our optimized Dockerfile, but if it happens:
1. Upgrade to paid plan ($7/month) for more memory during build
2. Or use smaller dependencies

### Service Starts but Crashes

**Check logs:**
1. In Render Dashboard → Your Service → Logs
2. Look for errors like:
   - "Model not loading" → Check disk space
   - "Port already in use" → Check PORT env var
   - "Permission denied" → Check Dockerfile user permissions

**Common fixes:**
- Ensure PORT=8000 in environment variables
- Verify Dockerfile has `EXPOSE 8000`
- Check health check endpoint is `/health` not `/`

### Slow Response Times

**Causes:**
1. **Cold start** (after 15 min idle) → Normal, wait 30s
2. **Large image** → Resize before uploading
3. **Free tier limits** → Consider upgrading

**Check inference time:**
- Should be 100-300ms for typical images
- > 1000ms suggests resource constraints

### Model Download Fails

**Symptom:** "Failed to download yolov8n.pt"

**Solutions:**
1. Check internet connectivity in Render
2. Verify GitHub is accessible (model downloads from GitHub releases)
3. Check logs for specific error

**Workaround:**
Pre-download model and include in Docker image (increases image size):
```dockerfile
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

---

## Updating Your Deployment

### Automatic Updates (Recommended)

Render automatically deploys when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update feature X"
git push origin main
```

Render will:
1. Detect the push
2. Rebuild the Docker image
3. Deploy automatically

### Manual Deployment

In Render Dashboard:
1. Go to your service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## Environment Variables

### Changing Model

Want to use a larger/better model?

1. In Render Dashboard → Your Service → Environment
2. Edit `MODEL_NAME`:
   - `yolov8n.pt` - Fastest (default)
   - `yolov8s.pt` - Better accuracy
   - `yolov8m.pt` - Great accuracy (needs paid tier)
3. Click **"Save Changes"**
4. Service will restart with new model

### Adding Custom Settings

Add any environment variable:
- `CONFIDENCE_THRESHOLD` - Default detection confidence
- `MAX_FILE_SIZE` - Maximum upload size
- `CORS_ORIGINS` - Allowed domains (use specific domains in production)

---

## Custom Domain (Paid Plans Only)

### Setup

1. Upgrade to paid plan ($7/month)
2. In Render Dashboard → Your Service → Settings
3. Add custom domain: `api.yourdomain.com`
4. Update DNS records as instructed by Render
5. Render automatically provisions SSL certificate

---

## Monitoring and Logs

### View Logs

**Real-time:**
1. Render Dashboard → Your Service → Logs
2. See all requests, errors, and model activity

**Download:**
1. Click "Download logs"
2. Get last 24 hours of activity

### Metrics

Free tier includes:
- Request count
- Response times
- Error rates
- Memory usage
- CPU usage

### Health Checks

Render pings `/health` every 30 seconds:
- ✅ Healthy: Returns 200 OK
- ❌ Unhealthy: Service restarts automatically

---

## Cost Breakdown

### Free Tier
- **Cost**: $0/month
- **Limitations**:
  - Sleeps after 15 min inactivity
  - 750 hours/month
  - Shared resources
- **Best for**: Portfolio, demos, learning

### Starter Plan
- **Cost**: $7/month
- **Benefits**:
  - Always on (no cold starts)
  - Better performance
  - More memory (512MB → 2GB)
  - Custom domains
- **Best for**: Small production apps

---

## Security Considerations

### Production Checklist

Before sharing widely:

1. **Restrict CORS**:
   ```yaml
   - key: CORS_ORIGINS
     value: "https://yourdomain.com,https://www.yourdomain.com"
   ```

2. **Add rate limiting** (code changes needed):
   - Limit requests per IP
   - Prevent abuse

3. **Monitor usage**:
   - Check Render dashboard regularly
   - Set up alerts for errors

4. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   ```

### API Key Protection

Current setup has no authentication. For production:
1. Add API key authentication
2. Use environment variables for keys
3. Implement request quotas

---

## Next Steps

After successful deployment:

1. ✅ **Test your live API**
   - Upload images
   - Check different models
   - Verify performance

2. ✅ **Share your project**
   - Add live URL to GitHub README
   - Update portfolio
   - Share on LinkedIn

3. ✅ **Monitor usage**
   - Check Render dashboard
   - Review logs
   - Track errors

4. ✅ **Integrate with Hugo** (optional)
   - See [Hugo Integration Guide](docs/04_hugo_integration.md)
   - Embed on your website

---

## Getting Help

### Render Support
- Documentation: https://render.com/docs
- Community: https://community.render.com/
- Status: https://status.render.com/

### Project Issues
- GitHub Issues: Your repo → Issues tab
- Check logs first
- Include error messages and screenshots

---

## Summary

**What you deployed:**
- ✅ FastAPI application
- ✅ YOLOv8 object detection
- ✅ Visual demo interface
- ✅ Docker container
- ✅ Automatic HTTPS
- ✅ Health monitoring

**Your URLs:**
- 📦 **GitHub**: `https://github.com/YOUR_USERNAME/ObjectDetection_ML_Deployment`
- 🚀 **Live API**: `https://your-app.onrender.com`
- 📚 **API Docs**: `https://your-app.onrender.com/docs`
- 🎨 **Demo UI**: `https://your-app.onrender.com/`

**Total time invested:** ~3 days
**Total cost:** $0 (free tier)
**Result:** Production-ready ML API ✨

Congratulations! Your object detection API is now live and accessible to the world! 🎉