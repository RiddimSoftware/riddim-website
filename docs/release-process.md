# Website Release Process

Riddim website releases use S3 artifact promotion rather than Amplify branch
promotion. A merge to `main` builds one immutable artifact, deploys that exact
artifact to validation, and leaves production unchanged until a human approves
the `production` GitHub Environment and runs the manual promotion workflow.

## Infrastructure

The deployment infrastructure lives in
`infrastructure/cloudformation/riddim-website-static-site.yml`.

It creates:

- an artifact S3 bucket with versioning and private access;
- private validation and production S3 hosting buckets;
- CloudFront distributions for validation and production;
- CloudFront Origin Access Control policies so S3 content is not public;
- a least-privilege IAM policy attached to the existing
  `riddim-website-deploy` GitHub OIDC role;
- optional, disabled-by-default production aliases and Route 53 cutover records
  for `riddimsoftware.com` and `www.riddimsoftware.com`.

Apply or update the stack from a privileged operator session:

```bash
aws cloudformation deploy \
  --region us-east-1 \
  --stack-name riddim-website-static-site \
  --template-file infrastructure/cloudformation/riddim-website-static-site.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    DeployRoleName=riddim-website-deploy \
    EnableProductionAliases=false \
    EnableRoute53CutoverRecords=false
```

After the stack exists, copy these stack outputs into GitHub Actions variables:

- `ARTIFACT_BUCKET`
- `VALIDATION_BUCKET`
- `VALIDATION_DISTRIBUTION_ID`
- `VALIDATION_BASE_URL`
- `PRODUCTION_BUCKET`
- `PRODUCTION_DISTRIBUTION_ID`
- `PRODUCTION_BASE_URL`

The repository secret `AWS_ROLE_ARN` must remain set to the existing OIDC role:
`arn:aws:iam::227530433709:role/riddim-website-deploy`. Do not add long-lived
AWS access keys.

## Production Request Logs

As of **2026-05-05**, the production CloudFront distribution
`E3RTZ0JDZLBX2I` writes standard access logs to:

- bucket: `riddim-website-cloudfront-accesslogs227530433709`
- prefix: `cloudfront/production/`

- Current retention target: **90 days**
- Cookie logging: **disabled**
- Bucket ownership mode: **BucketOwnerPreferred**
- Purpose: directional request counts, top paths, referrers, and 4xx/5xx trend
  checks without client-side analytics

This log bucket is currently managed outside the static-site CloudFormation
stack because CloudFront standard logging still requires S3 ACL support. Do
not switch this bucket to `BucketOwnerEnforced`; standard log delivery would
stop because CloudFront still writes with ACL semantics.

To fetch a recent batch of logs locally (replace the profile name with any
AWS profile that has read access to the log bucket):

```bash
AWS_PROFILE=<profile-with-s3-access> aws s3 sync \
  "s3://riddim-website-cloudfront-accesslogs227530433709/cloudfront/production/" \
  ./tmp/cloudfront-logs
```

If you need to force a controlled smoke test before the public
`riddimsoftware.com` DNS cutover, hit the current static-site production
CloudFront hostname directly and then look for a fresh object under the log
prefix. Before DNS cutover, the default CloudFront hostname may still return
`403 AccessDenied`; that is acceptable for log-seeding purposes as long as the
request appears in the next delivered log batch.

```bash
for _ in 1 2 3 4 5; do
  curl -sS -o /dev/null -w '%{http_code}\n' https://d2qjhrs4yekq6x.cloudfront.net/
  sleep 1
done

AWS_PROFILE=<profile-with-s3-access> aws s3api list-objects-v2 \
  --bucket riddim-website-cloudfront-accesslogs227530433709 \
  --prefix cloudfront/production/ \
  --query 'reverse(sort_by(Contents,&LastModified))[:10].[Key,LastModified,Size]' \
  --output table
```

Useful one-liners once the `.gz` files are downloaded:

```bash
find ./tmp/cloudfront-logs -name '*.gz' -print0 | xargs -0 zcat | awk '{print $8}' | sort | uniq -c | sort -rn | head -20
find ./tmp/cloudfront-logs -name '*.gz' -print0 | xargs -0 zcat | awk '{print $10}' | sort | uniq -c | sort -rn | head -20
find ./tmp/cloudfront-logs -name '*.gz' -print0 | xargs -0 zcat | awk '{print $9}' | grep -E '^[45]' | sort | uniq -c
```

CloudFront standard logs are delayed delivery; expect roughly **within one
hour** after live traffic or a smoke-test request.

## Validation Deployment

`.github/workflows/deploy-validation.yml` runs on every push to `main`.

The workflow:

1. checks out the repository;
2. configures AWS credentials through GitHub OIDC;
3. runs `python3 scripts/validate.py`;
4. builds `/tmp/<sha>.tar.gz` with `scripts/build_artifact.sh`;
5. uploads `riddim-website/<sha>.tar.gz` with `scripts/upload_artifact.sh`;
6. deploys that artifact to the validation bucket with
   `scripts/deploy_artifact.sh validation <sha>`;
7. writes `version.json`;
8. invalidates validation CloudFront;
9. smoke checks the validation CloudFront URL.

Artifacts are immutable by key. If `riddim-website/<sha>.tar.gz` already
exists, the upload script accepts it only when the stored `sha256` metadata
matches the local artifact. A mismatch fails the workflow.

The validation URL is the AWS-provided CloudFront domain from the
`ValidationCloudFrontUrl` stack output. It must not be a `riddimsoftware.com`
hostname unless a later ticket intentionally adds a branded validation domain.

## Production Promotion

`.github/workflows/promote-production.yml` is manual only.

To promote:

1. open **Actions → Promote Production**;
2. enter the already-built commit SHA from a successful validation deployment;
3. approve the `production` GitHub Environment gate;
4. let the workflow deploy the existing artifact to production, write
   `version.json`, invalidate CloudFront, and run smoke checks.

The production workflow does not rebuild the site. It downloads
`riddim-website/<sha>.tar.gz` from the artifact bucket and deploys those bytes.

Rollback uses the same workflow: enter a previously validated commit SHA and
approve the `production` environment gate. The logs print the promoted artifact
SHA and the deployed `version.json` records `commitSha`, `buildTime`,
`deployedAt`, `environment`, and `artifactKey`.

## Cache Behavior

Deployment metadata is set in `scripts/deploy_artifact.sh`.

- HTML, `version.json`, and `artifact-manifest.json` use short revalidated
  caching.
- `/.well-known/apple-app-site-association` is uploaded as JSON and keeps the
  one-hour cache behavior from the Amplify header configuration.
- `/apple-app-site-association.json`, `/robots.txt`, and `/sitemap.xml` keep
  explicit content types and short cache windows.
- Filenames containing an eight-character-or-longer hex hash receive
  `public,max-age=31536000,immutable`.
- Other static assets use a conservative one-hour revalidated cache.
- Every deployment issues a CloudFront invalidation for `/*`.

Unknown routes return the dedicated `404.html` page with HTTP 404. CloudFront
also rewrites extensionless directory routes such as `/double-dozen/` to the
matching `index.html` object before the S3 origin lookup, so canonical product
pages resolve correctly on the static origin.

## Human-Gated Cutover

Do not perform these steps from an autonomous implementation session.

After validation and production promotion have been verified on their
CloudFront URLs, a human can approve public DNS cutover:

1. confirm a us-east-1 ACM certificate covers `riddimsoftware.com` and
   `www.riddimsoftware.com`;
2. update the CloudFormation stack with:

   ```bash
   aws cloudformation deploy \
     --region us-east-1 \
     --stack-name riddim-website-static-site \
     --template-file infrastructure/cloudformation/riddim-website-static-site.yml \
     --capabilities CAPABILITY_NAMED_IAM \
     --parameter-overrides \
       DeployRoleName=riddim-website-deploy \
       EnableProductionAliases=true \
       ProductionAcmCertificateArn=<us-east-1-certificate-arn> \
       EnableRoute53CutoverRecords=false
   ```

3. verify the production distribution accepts the custom domains;
4. approve DNS cutover explicitly;
5. either update DNS manually or rerun the stack with
   `EnableRoute53CutoverRecords=true PublicHostedZoneId=<zone-id>`;
6. verify `https://riddimsoftware.com/version.json` and
   `https://www.riddimsoftware.com/version.json` report the promoted SHA;
7. approve disconnecting or disabling the old Amplify app only after the new
   production path is verified.

The Amplify app `d1fpbj2kbbps1r` in `us-east-1` should remain connected until
that final approval is captured.
