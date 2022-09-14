import argparse, socket, time, json, datetime, platform, psutil, requests, pprint, uuid
import os 

# parse args
parser = argparse.ArgumentParser(description='Monitoring script to send system info to a tracking server')
parser.add_argument('-d', '--dest', default='http://localhost:8080/', help='API Endpoint for Monitoring Data (Defaults to http://localhost:8080/)')
parser.add_argument('-i', '--interval', default=10, type=int, help='Interval between checks (Seconds. Defaults to 5 seconds)')
parser.add_argument('-a', '--attempts', default=30, type=int, help='Attempts to send data when sending failes (Defaults to 30)')
parser.add_argument('-t', '--timeout', default=60, type=int, help='Timeout between resend attempts (Seconds. Defaults to 60. If attempts is reached script will die)')
args = parser.parse_args()

# Factor in sleep for bandwidth checking
if args.interval >= 2:
    args.interval -= 2

def main():
    # Hostname Info
    hostname = socket.gethostname()
    #print("Hostname:", hostname)

    # CPU Info
    cpu_count = psutil.cpu_count()
    cpu_usage = psutil.cpu_percent(interval=1)
    #print("CPU:Count: "+ str(cpu_count) + " Usage: " + str (cpu_usage) + "%")
    
    

    # Memory Info
    memory_stats = psutil.virtual_memory()
    memory_total = memory_stats.total
    memory_used = memory_stats.used
    memory_used_percent = memory_stats.percent
    #print("Memory: " + str(memory_used_percent) + "%  Total: " + str(memory_total / 1e+6) + " MBs, Used: " +str( memory_used / 1e+6) +" MB")


    # Bandwidth Info
    network_stats = get_bandwidth()
    #print("Network:Traffic in:" +str (network_stats["traffic_in"] /1e+6) + " Traffic out: " + str(network_stats["traffic_out"] / 1e+6))
    #print("Network:Traffic in:" +str (network_stats["traffic_in"] / 1e+6) +"MB" + " Traffic out: " + str(network_stats["traffic_out"] / 1e+6 )+ "MB")


    # Time Info
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    uptime = int(time.time() - psutil.boot_time())
    #print("System Uptime:" +str(uptime))

    #Load Average 
    load1, load5, load15 = os.getloadavg()

    
    print(hostname, cpu_count, cpu_usage, memory_used_percent, memory_total/1e+6, memory_used/1e+6, uptime, load1, load5, load15)


def get_bandwidth():
    # Get net in/out
    net1_out = psutil.net_io_counters().bytes_sent
    net1_in = psutil.net_io_counters().bytes_recv

    time.sleep(1)

    # Get new net in/out
    net2_out = psutil.net_io_counters().bytes_sent
    net2_in = psutil.net_io_counters().bytes_recv

    # Compare and get current speed
    if net1_in > net2_in:
        current_in = 0
    else:
        current_in = net2_in - net1_in

    if net1_out > net2_out:
        current_out = 0
    else:
        current_out = net2_out - net1_out

    network = {"traffic_in" : current_in, "traffic_out" : current_out}
    return network, argparse

def send_data(data):
    # Attempt to send data up to 30 times
    for attempt in range(args.attempts):
        try:
            # endpoint = monitoring server
            endpoint = args.dest
            response = requests.post(url = endpoint, data = data)
            print("\nPOST:")
            print("Response:", response.status_code)
            print("Headers:")
            pprint.pprint(response.headers)
            print("Content:", response.content)
            # Attempt printing response in JSON if possible
            try:
                print("JSON Content:")
                pprint.pprint(response.json())
            except:
                print("No JSON content")
            break
        except requests.exceptions.RequestException as e:
            print("\nPOST Error:\n",e)
            # Sleep 1 minute before retrying
            time.sleep(args.timeout)
    else:
        # If no connection established for attempts*timeout, kill script
        exit(0)




print_title = True
while True:
    if print_title:
        print("Hostname", "CPU_Count", "CPU_Usage_Perct", "Mem_Used_Perct", "Total_Mem", "Mem_Used", "Uptime", "Load1", "Load5", "Load15")
        print_title = False
    else:
        main()
        #print("-----------------------------------------------------------------")
        time.sleep(args.interval)

