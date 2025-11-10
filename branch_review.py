# Updated branch_review.py content

# (Previous content omitted for brevity...) 



def show_branch_changes(branch_name):
    """Show the changes in a specific branch compared to main."""
    print(f"\n=== Changes in branch '{branch_name}' ===")

    # Show commit log for the branch
    print("\nCommits in this branch:")
    log_output = run_git_command(f"git log --oneline main..{branch_name}")
    if log_output:
        print(log_output)
    else:
        print("(No commits found for this branch.)")

    # Show diff
    print(f"\nDiff from main to {branch_name}:")
    diff_output = run_git_command(f"git diff main..{branch_name}")
    if diff_output:
        print(diff_output)
    else:
        print("(No changes found in this branch compared to main.)")

# (Rest of the file content omitted for brevity...) 
