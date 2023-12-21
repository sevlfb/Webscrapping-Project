def create_df(reviews):
    reviews_names = {tag_[0] for review in reviews for tag_ in review}        
    reviews_list = []
    for review in reviews:
        line = []
        for i, review_name in enumerate(reviews_names):
            temp = [tag_[0] for tag_ in review]
            if review_name in temp:
                line.append(review[temp.index(review_name)][1])
            else:
                line.append('')
        reviews_list.append(line)
        
    print(reviews_list)
    
    
def create_element_list():
    try:
    infos = []
    for tag in tags:
        if tag in elements:
            infos.append((tag, elements.index(tag)))
    infos.append(('end', len(elements)))
    if len(infos)>0:
        infos.sort(key=(lambda x: x[1]))
    info_dic = {}
    for tag in tags:
        info_dic[tag] = []
    for i, info in enumerate(infos[:-1]):
        info_dic[info[0]] = elements[info[1]+1:infos[i+1][1]]
    print(info_dic if info_dic else print("No additionnal categories"))
    except:
        info_dic = {}
        for tag in tags:
            info_dic[tag] = ''
        print("No job detail section !") 