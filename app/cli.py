# -*- coding: utf-8 -*-

"""Console script for tuesday."""
import click

from app.libs import member as memberlib


@click.group()
def cli_group():
    pass


@cli_group.command()
@click.option('--email', prompt='email',
              help='The email of the Member to delete.')
def delete_user(email):
    """Delete a user"""
    member = memberlib.get_by_email(email)
    if member:
        memberlib.delete(member['id'])
        print(f"Member with the email : {email} - deleted successfully.")
    else:
        print(f"Member with the email : {email} - not found.")


cli = click.CommandCollection(sources=[cli_group])

if __name__ == "__main__":
    cli()
