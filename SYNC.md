# Git Workflow

Remote: `https://github.com/rishilsodha-cell/Rishil-dashboard`

## Daily workflow

After making changes:

```
git add .
git commit -m "describe what changed"
git push
```

To pull down changes made elsewhere (e.g. via the GitHub web UI):

```
git pull
```

To check what's changed locally:

```
git status
```

## If something goes wrong

- **Merge conflict:** edit the conflicted file (look for `<<<<<<<` markers), save it, then `git add <file> && git commit`
- **Undo uncommitted local changes:** `git checkout -- <file>`
- **See recent commits:** `git log --oneline -10`
- **See what changed in a file:** `git diff <file>`
