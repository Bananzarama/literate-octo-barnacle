import random

def pull_from_list(wordlist):
    """
    pull a from a list
    newWord = pull_from_list('en_US.txt')
    """
    file_handle = open(wordlist)
    words = file_handle.readlines()
    newHash = random.choice(words).strip()
    return newHash
    
def main():
    newWord = pull_from_list('E:\\rockyou.txt')
    print("newWord:", newWord)

if __name__ == '__main__':
    main()
