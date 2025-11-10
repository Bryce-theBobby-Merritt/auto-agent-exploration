#!/usr/bin/env python3
"""
Branch Review and Merge Tool for the Simple Agent Container Workflow

This script helps the host user review feature branches created by the agent
and merge approved changes into the main branch.

Usage:
    python branch_review.py

The script will:
1. Show all available branches
2. Allow selection of a branch to review
3. Show the changes in that branch
4. Allow the user to approve/merge or reject the branch
"""

import subprocess
import sys
from pathlib import Path


def run_git_command(command, cwd=None):
    """Run a git command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        print(f"Error output: {e.stderr}")
        return None


def get_branches():
    """Get all branches except the current one."""
    branches_output = run_git_command("git branch -a")
    if not branches_output:
        return []

    branches = []
    current_branch = None

    for line in branches_output.split('\n'):
        line = line.strip()
        if line.startswith('*'):
            current_branch = line[2:].strip()
        else:
            branches.append(line)

    return branches, current_branch


def show_branch_changes(branch_name):
    """Show the changes in a specific branch compared to main."""
    print(f"\n=== Changes in branch '{branch_name}' ===")

    # Show commit log for the branch
    print("\nCommits in this branch:")
    log_output = run_git_command(f"git log --oneline main..{branch_name}")
    if log_output and len(log_output) > 0:
        print(log_output)
    else:
        print("(No commits found for this branch.)")

    # Show diff
    print(f"\nDiff from main to {branch_name}:")
    diff_output = run_git_command(f"git diff main..{branch_name}")
    if diff_output and len(diff_output) > 0:
        print(diff_output)
    else:
        print("(No changes found in this branch compared to main.)")


def merge_branch(branch_name):
    """Merge the specified branch into main."""
    print(f"\nMerging branch '{branch_name}' into main...")

    # Switch to main branch
    if run_git_command("git checkout main") is None:
        print("Failed to switch to main branch")
        return False

    # Merge the branch
    merge_result = run_git_command(f"git merge {branch_name}")
    if merge_result is None:
        print("Merge failed")
        return False

    print("Merge successful!")
    print(merge_result)

    # Optionally delete the merged branch
    delete_choice = input(f"\nDelete the merged branch '{branch_name}'? (y/n): ").lower().strip()
    if delete_choice == 'y':
        if run_git_command(f"git branch -d {branch_name}") is not None:
            print(f"Branch '{branch_name}' deleted")
        else:
            print(f"Failed to delete branch '{branch_name}'")

    return True


def reject_branch(branch_name):
    """Reject (delete) a branch without merging."""
    delete_choice = input(f"Are you sure you want to delete branch '{branch_name}' without merging? (y/n): ").lower().strip()
    if delete_choice == 'y':
        if run_git_command(f"git branch -D {branch_name}") is not None:
            print(f"Branch '{branch_name}' deleted")
            return True
        else:
            print(f"Failed to delete branch '{branch_name}'")
            return False
    return False


def main():
    """Main function for the branch review tool."""
    print("Simple Agent - Branch Review Tool")
    print("=" * 50)

    # Check if we're in a git repository
    if not Path(".git").exists():
        print("Error: Not in a git repository. Please run this from the project root.")
        sys.exit(1)

    # Get current branch
    current_branch = run_git_command("git rev-parse --abbrev-ref HEAD")
    if not current_branch:
        print("Error: Could not determine current branch")
        sys.exit(1)

    print(f"Current branch: {current_branch}")

    # Get all branches
    branches, _ = get_branches()
    if not branches:
        print("No other branches found.")
        print("\nThe agent will create feature branches when it makes changes.")
        print("Run this tool again after the agent has created some branches.")
        return

    print(f"\nAvailable branches ({len(branches)}):")
    for i, branch in enumerate(branches, 1):
        print(f"  {i}. {branch}")

    # Branch selection
    while True:
        try:
            choice = input("\nSelect a branch to review (number or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return

            branch_index = int(choice) - 1
            if 0 <= branch_index < len(branches):
                selected_branch = branches[branch_index]
                break
            else:
                print(f"Please enter a number between 1 and {len(branches)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")

    # Show branch changes
    show_branch_changes(selected_branch)

    # Decision prompt
    while True:
        decision = input(f"\nWhat would you like to do with branch '{selected_branch}'?\n"
                        "  1. Merge into main\n"
                        "  2. Reject (delete branch)\n"
                        "  3. Show more details\n"
                        "  4. Back to branch list\n"
                        "Choice: ").strip()

        if decision == '1':
            if merge_branch(selected_branch):
                print("Branch merged successfully!")
            else:
                print("Merge failed")
            break
        elif decision == '2':
            if reject_branch(selected_branch):
                print("Branch rejected and deleted")
            break
        elif decision == '3':
            # Show more details
            print("\n=== Additional Details ===")
            print("\nFiles changed:")
            files_output = run_git_command(f"git diff --name-only main..{selected_branch}")
            if files_output:
                print(files_output)
            else:
                print("(No files changed)")

            print("\nBranch status:")
            status_output = run_git_command(f"git status {selected_branch} --porcelain")
            if status_output:
                print(status_output)
            else:
                print("(Branch is clean)")

        elif decision == '4':
            # Back to branch list
            main()
            return
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()