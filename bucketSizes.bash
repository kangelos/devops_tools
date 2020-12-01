# angelos
export LC_NUMERIC=en_US.UTF-8
yesterday=$(date -d "1 day ago" '+%Y-%m-%d')T00:00
today=$(date '+%Y-%m-%d')T00:00


echo "Bucket Name ;Size (Mb)"
  buckets=$(aws s3 ls | awk '{print $3}')
  for buck in $buckets
  do
    echo -n $buck";"
      TZ=UTC now=$(date +%s)
      now=$(($now-43200))
      region=$(aws s3api  get-bucket-location --bucket $buck | jq .LocationConstraint)
      if [[ $region == "" ]]
      then 
          xtra_args="--region $region"
      fi
      size=$(aws cloudwatch get-metric-statistics --namespace AWS/S3 --metric-name BucketSizeBytes --dimensions Name=BucketName,Value=${buck} Name=StorageType,Value=StandardStorage --start-time $yesterday --end-time $today --period 86400 --statistic Average $xtra_args | jq .Datapoints[].Average)
     if [[ $size != "" ]]
      then
        echo -n $(($size/1048576))
      fi
  printf "\n"
done
