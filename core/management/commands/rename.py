from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):

    help = 'Renames a Django Project.'

    def add_arguments(self, parser):
        parser.add_argument('current_name', type=str,
                            help='Current name of your project.')
        parser.add_argument('new_name', type=str,
                            help='New name of your Django Project.')

    def handle(self, *args, **kwargs):
        current_name = kwargs['current_name']
        new_name = kwargs['new_name']
        files_to_rename = ['manage.py']

        file_to_rename = current_name + '/settings/base.py'
        files_to_rename.append(file_to_rename)
        file_to_rename = current_name + '/wsgi.py'
        files_to_rename.append(file_to_rename)

        folder_to_rename = current_name

        for f in files_to_rename:
            with open(f, 'r') as file:
                filedata = file.read()

            filedata = filedata.replace(current_name, new_name)

            with open(f, 'w') as file:
                file.write(filedata)

        os.rename(folder_to_rename, new_name)

        self.stdout.write(self.style.SUCCESS(
            'Project has been renamed to %s' % new_name))
