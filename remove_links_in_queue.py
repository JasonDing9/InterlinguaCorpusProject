links_file = open("link_queue.txt", "r")
link_queue = links_file.readlines()

go = []
count = 0
index = 0
while index < len(link_queue):
    if link_queue[index].find("interforo") == -1:
        go.append(link_queue[index])
        del link_queue[index]
    else:
        index = index + 1
        count = count + 1
        


print(count)
links_file = open("link_queue.txt", "w")
for link in go:
    links_file.write(link)
