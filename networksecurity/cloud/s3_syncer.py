import os


# class S3Sync:
#     def sync_folder_to_s3(self,folder,aws_bucket_url):
#         command = f"aws s3 sync {folder} {aws_bucket_url} "
#         os.system(command)

#     def sync_folder_from_s3(self,folder,aws_bucket_url):
#         command = f"aws s3 sync  {aws_bucket_url} {folder} "
#         os.system(command)
class S3Sync:

    def __init__(self, enabled=False):
        self.enabled = enabled

    def sync_folder_to_s3(self, folder, aws_bucket_url):
        if not self.enabled:
            print("Skipping S3 upload sync (disabled).")
            return
        os.system(f"aws s3 sync {folder} {aws_bucket_url}")

    def sync_folder_from_s3(self, folder, aws_bucket_url):
        if not self.enabled:
            print("Skipping S3 download sync (disabled).")
            return
        os.system(f"aws s3 sync {aws_bucket_url} {folder}")
