from urllib.parse import urlparse
import urllib.request
import socket
import time
import sys


def progressBar(count_value, total, suffix=''):
    bar_length = 100
    filled_up_Length = int(round(bar_length * count_value / float(total)))
    percentage = round(100.0 * count_value/float(total), 1)
    bar = '=' * filled_up_Length + '-' * (bar_length - filled_up_Length)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percentage, '%', suffix))
    sys.stdout.flush()


def buildList():
    urllib.request.urlretrieve(
        'https://publicsuffix.org/list/public_suffix_list.dat', 'public_suffix_list.dat')
    with open("public_suffix_list.dat", "r") as input:
        with open("clean_psl.dat", "w") as output:
            for line in input:
                if line.strip():
                    if not line.strip("\n").startswith('//'):
                        if not line.strip("\n").startswith('*'):
                            output.write(line)
    with open("clean_psl.dat", "r") as lines:
        data = lines.read().split('\n')
    return data


def ping_server(server: str, port: int, timeout=1):
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
    except OSError as error:
        return False
    else:
        s.close()
        return True


def scrape_tld(server: str, port: int, timeout=3):
    domainSplit = server.split(".")
    secondLevelDomain = domainSplit[1]
    topLevelDomain = domainSplit[2]
    tldList = buildList()
    print("TLDs Found:", len(tldList))
    print("are you sure you would you like to scrape \"" +
          secondLevelDomain + "\" for TLDs? Y/N")
    reply = input()
    if reply is "Y" or reply is "y":
        with open("output.txt", "w") as output:
            count = 0
            output.write("Domain: "+ secondLevelDomain +
                         "  Initial TLD: " + topLevelDomain + "\n")
            for domain in tldList:
                newDomain = secondLevelDomain + "." + domain
                request = ping_server(newDomain, 443)
                if request:
                    output.write(newDomain + "\n")
                count += 1
                time.sleep(.0001)
                progressBar(count, len(tldList))
            output.write("TLDs Found: " + count)
    else:
        print('Goodbye!')
        return (1)


def main():
    targetURL = None
    targetServer = None
    if len(sys.argv) >= 2:
        targetURL = sys.argv[1]
    if targetURL is None:
        print("No url found")
    else:
        targetServer = urlparse(targetURL).netloc
        response = ping_server(targetServer, 443)
        if response:
            print("server status:", response)
            print("would you like to scrape \"" +
                  targetServer + "\" for TLDs? Y/N")
            reply = input()
            if reply is "Y" or reply is "y":
                scrape_tld(targetServer, 443)
            else:
                print('Goodbye!')
                return (1)


if __name__ == '__main__':
    main()
