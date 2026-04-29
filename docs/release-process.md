# Website Release Process

Riddim website releases use the shared website scripts from
`RiddimSoftware/riddim-release`.

1. Open or update a pull request from a branch in this repository.
2. The `Website Preview` workflow deploys an Amplify branch named `pr-<number>`.
3. Test locally or with the preview URL posted on the PR.
4. Merge the PR after approval. Use the normal merge-commit path so the
   previewed commit remains present on `main`.
5. The `Website Promote` workflow verifies that the previewed commit is on
   `main`, then waits for the `website-production` GitHub Environment approval.
6. After approval, the exact preview artifact is deployed to the Amplify `main`
   branch, which serves `www.riddimsoftware.com`.
7. The preview branch is deleted after production deployment. Unmerged PRs have
   their preview branch deleted by `Website Preview Cleanup`.

Fork PRs do not receive automatic cloud previews because preview deployment uses
AWS credentials.
