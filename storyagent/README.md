# StoryAgent automation

Cloudinary cloud name: `oe5bvdqa` (public identifier only). Never commit API secrets.

Required Render environment variables: `CLOUDINARY_URL` (secret, Cloudinary-provided), `METRICOOL_API_TOKEN` (secret), `METRICOOL_USER_ID` (if required by API), `METRICOOL_BLOG_ID=7226872`.

Daily pipeline: generate original stories and JPEGs, upload via Cloudinary, schedule through Metricool with autoPublish enabled, verify posts, and log failures. Deployment remains pending until secure credentials and Render workspace are confirmed.

TikTok photo posts need JPEG/WebP URLs. The public cloud name alone does not authorize uploads.
