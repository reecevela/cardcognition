set -e

host="$1"
shift
cmd="$@"

until nc -z -v -w30 $host; do
  >&2 echo "Web service is unavailable - sleeping"
  sleep 1
done

>&2 echo "Web service is up - executing command"
exec $cmd