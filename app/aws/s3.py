import boto3

class S3Client():
    def __init__(self, bucket_name: str, region: str, tmp_bucket = False):
        """
        Connect to a S3 bucket.

        Args:
            bucket_name: the name of the bucket
            region: a region in which the bucket is located
            tmp_bucket: should this bucket be deleted when client is closed, not recommended to use outside of testing
        """
        self.client = boto3.client("s3")
        self.bucket = bucket_name
        self.bucket_region = region
        self.tmp_bucket = tmp_bucket

        buckets = self.client.list_buckets()

        bucket_exists = False

        if bucket_name == [b["Name"] for b in buckets["Buckets"]][0]:
            bucket_exists = True

        if not bucket_exists:
            self.__create_bucket()

    def upload_obj(self, file_name: str, data):
        """
        Upload specified data stream to the bucket.

        Args:
            file_name: the name under which the file will be stored, including the folder name
            data: the data stream to send
        """
        result = self.client.upload_fileobj(Fileobj=data, Bucket=self.bucket, Key=file_name)

    @staticmethod
    def __print_bytes_sent(count):
        print("Bytes sent:", count)

    def upload_data(self, file_name: str, data):
        """
        Upload specified data stream to the bucket.

        Args:
            file_name: the name under which the file will be stored, including the folder name
            data: the data stream to send
        """
        self.upload_obj(f"{file_name}.json", data)

    def upload_image(self, file_name: str, data):
        """
        Upload specified image stream to the bucket.

        Args:
            file_name: the name under which the file will be stored, including the folder name
            data: the image stream to send
        """
        self.upload_obj(f"{file_name}.jpeg", data)

    def file_exists(self, file_name: str) -> bool:
        """
        Check if the specified file already exists in the bucket

        Args:
            file_name: the name of the file, including folder name

        Returns:
            bool
        """
        return False

    def close(self):
        if self.tmp_bucket:
            self.client.delete_bucket()
        self.client.close()

    def __create_bucket(self):
        response = self.client.create_bucket(
            ACL="public-read",
            Bucket=self.bucket, 
            CreateBucketConfiguration=
            {
                "LocationConstraint": self.bucket_region
            },
            ObjectLockEnabledForBucket=False,
            ObjectOwnership="BucketOwnerPreferred"
            )