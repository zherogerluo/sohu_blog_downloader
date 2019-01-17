import json

def json_to_html():
    with open("blog_data.json", "r") as file:
        blog_data = json.load(file)

    with open('blog_content.html', 'w') as file:
        file.write('<html>\n')
        file.write('<body>\n')
        for _, date, title, tag, body in blog_data:
            # file.write('<details><summary>%s&nbsp;&nbsp;&nbsp;&nbsp;%s</summary>\n' % (date, title))
            file.write('<p>%s</p>\n' % date)
            file.write('<h3 style="text-align:center;">%s</h3>\n' % title)
            if tag:
                file.write('<h5 style="text-align:center;font-weight:normal">标签:&nbsp;&nbsp;%s<br></h5>\n' % tag)
            file.write(body)
            file.write('<br>\n<hr>\n')
            # file.write('</details>\n')
            print("Content written to file for blog %s %s" % (date, title))

        file.write('</body>\n')
        file.write('</html>\n')

if __name__ == '__main__':
    json_to_html()