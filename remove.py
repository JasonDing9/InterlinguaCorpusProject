traversed_links_file = open("traversed_links.txt", "r")
traversed_links = traversed_links_file.readlines()

go = []
count = 0
index = 0
while index < len(traversed_links):
    if traversed_links[index].find("interforo") == -1 and traversed_links[index].find("blogspot") == -1 and traversed_links[index].find("wordpress") == -1:
        index = index + 1
    else:
        count = count + 1
        go.append(traversed_links[index])
        del traversed_links[index]


print(count)
traversed_links_file = open("traversed_links.txt", "w")
for link in traversed_links:
    traversed_links_file.write(link)

traversed_links_file = open("interforo.txt", "w")
for link in go:
    traversed_links_file.write(link)
