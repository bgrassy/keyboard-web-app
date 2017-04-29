from flask import Flask, render_template, request, send_file
from layout import genetic, alphabetize, layout_score, draw_image
import io, os
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def form():
    return render_template("login.html")

@app.route('/layout', methods=["GET", "POST"])
def layout():
    if request.method == 'POST':    
        print("string: ")
        string = request.form["string"]
        max_gen = request.form["gen"]
        removed_string = request.form["removed"]
        string = alphabetize(string)
        sums = []
        same_max_count = 0
        curr_max = 0
        final_layouts= []
        gen = 0
        removed_chars = set()
        if removed_string != "":
            for ch in removed_string:
                removed_chars.add(ch)

        for i in range(int(max_gen)):
            vals = genetic(string, sums, same_max_count, curr_max, gen, final_layouts, removed_chars)
            sums = vals[0] 
            same_max_count = vals[1]
            curr_max = vals[2]
            final_layouts = vals[3]
            gen = gen + 1
            print(gen)
            if same_max_count >= 20:
                break

        print("Max: " + str(max(sums)))
        maxSum = max(sums)
        max_layout = []
        for layout in final_layouts:
            if layout_score(layout, string) == maxSum:
                max_layout = layout
                break
        print(max_layout)
        draw_image(max_layout)
        return render_template("layout.html")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
