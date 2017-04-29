import random, math, os, copy, re
from PIL import Image, ImageDraw
# Initializes correspondences between the keys and various stats
keys = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f',
        'g', 'h', 'j', 'k', 'l', ';', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.']
fingers = [1, 2, 3, 4, 4, 5, 5, 6, 7, 8, 1, 2, 3, 4, 4, 5, 5, 6, 7, 8, 1, 2,
           3, 4, 4, 5, 5, 6, 7]
hand = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0,
        0, 0, 1, 1, 1, 1]
distances = [1.9, 1.9, 1.9, 1.9, 2.5, 3, 1.9, 1.9, 1.9, 1.9, 0, 0, 0, 0, 1.9,
             1.9, 0, 0, 0, 0, -2.1, -2.1, -2.1, -2.1, -3.5, -2.1, -2.1, -2.1, -2.1]
rows = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2,
        2, 2, 2, 2, 2, 2]
locs = [[0.75, 0.75], [2.65, 0.75], [4.55, 0.75], [6.45, 0.75], [8.35, 0.75],
        [10.25, 0.75], [12.15, 0.75], [14.05, 0.75], [15.95, 0.75], [17.85, 0.75],
        [1.2, 2.5], [3.1, 2.5], [5.0, 2.5], [6.9, 2.5], [8.8, 2.5], [10.7, 2.5],
        [12.6, 2.5], [14.5, 2.5], [16.4, 2.5], [18.3, 2.5], [2.25, 4.4], [4.15, 4.4],
        [6.05, 4.4], [7.95, 4.4], [9.85, 4.4], [11.75, 4.4], [13.65, 4.4],
        [15.55, 4.4], [17.45, 4.4]]
current_locs = [10, 11, 12, 13, 16, 17, 18, 19]
start_locs = [10, 11, 12, 13, 16, 17, 18, 19]
ideal_ratio = [7, 10, 15, 18, 18, 15, 10, 7]
gen = 0
same_max_count = 0
sums = []
final_layouts = []
removed_chars = set()


# Takes a keyboard layout, and returns a randomly shuffled copy of it.
# Ignores the characters which are fixed.
def shuffle_layout(layout, removed_chars):
    random.seed()
    removed_layout = []
    new_layout = []
    index = 0
    for i in [x for x in layout if x not in removed_chars]:
        removed_layout.append(i)
    random.shuffle(removed_layout)
    for i in range(len(keys)):
        if keys[i] in removed_chars:
            new_layout.append(keys[i])
        else:
            new_layout.append(removed_layout[index])
            index += 1
    return new_layout


# Takes two characters or two integers corresponding to the indexes of the characters
# in the string. Returns the distance between the two keys on the layout.
def key_dist(key1, key2):
    if key1 in keys:
        key1 = keys.index(key1)
        key2 = keys.index(key2)
    key1 = locs[key1]
    key2 = locs[key2]
    return math.sqrt((key1[0] - key2[0]) ** 2 + (key1[1] - key2[1]) ** 2)

# Takes a character corresponding to a key and a keyboard layout. Returns the
# distance required to go to the key, and factors in the distance of other fingers
# returning to the home row.
def char_dist(ch, layout):
    distance = 0
    count = 0
    index = layout.index(ch)
    finger = fingers[index] - 1
    current_loc = current_locs[finger]
    distance += key_dist(index, current_loc) / 5.0
    current_locs[finger] = index
    count = count + 1
    for num in range(8):
        if (num + 1) != finger:
            if current_locs[num] != start_locs[num]:
                distance += key_dist(current_locs[num], start_locs[num]) / 5.0
                current_locs[num] = start_locs[num]
                count += 1
    return distance, count


# Takes the ratio of finger usage for a current layout and compares it to
# the "ideal" proportions, returning a distance that is scaled to be between
# zero and one, with zero as the maximum distance and 1 and the minimum.
def ratio_distance(ratios):
    count = 0
    for i in range(8):
        count += (ratios[i] - ideal_ratio[i]) ** 2
    return (7098 - count) / 7098


# Takes a keyboard layout and the string it is generating it from. Returns
# an overall score for the layout, taking the finger alternation, hand alternation,
# distance traveled and finger ratios into account.
def layout_score(layout, string):
    count = 0
    distance = 0
    alt_sum = 0
    finger_sum = 0
    finger_count = [0] * 8
    for i in range(len(string)):
        ch = string[i]
        distance_diff, count_diff = char_dist(ch, layout)
        count = count + count_diff
        distance = distance + distance_diff
        finger = fingers[layout.index(ch)] - 1
        finger_count[finger] += 1
        # Calculates the alternation counts and the finger ratios.
        if i != len(string) - 1:
            index_1 = layout.index(string[i])
            index_2 = layout.index(string[i + 1])
            finger_1 = fingers[index_1]
            finger_2 = fingers[index_2]
            # Increments the finger counter if the fingers are different or the keys are the same
            if finger_1 != finger_2 or string[i] == string[i + 1]:
                finger_sum = finger_sum + 1
            # Increments the hand counter if keys are on different hands
            if hand[index_1] != hand[index_2]:
                alt_sum += 1
    finger_count = [num / len(string) * 100 for num in finger_count]
    return 1 - (distance / count) + (alt_sum + finger_sum) / (len(string) - 1) + ratio_distance(finger_count)


# Takes a string and removes all non-alphabetical, comma, period, or
# semicolon keys.
def alphabetize(string):
    string = string.lower().replace("\n", "").replace("\t", "")
    regex = re.compile('[^a-zA-Z.,;]')
    string = regex.sub('', string)
    return string


# Takes a keyboard layout. Randomly chooses two keys and swaps their
# position.
def mutate(layout, removed_chars):
    rands = random.sample(set(keys) - removed_chars, 2)
    index_1 = layout.index(rands[0])
    index_2 = layout.index(rands[1])
    layout[index_1], layout[index_2] = layout[index_2], layout[index_1]
    return layout


# Takes a list of layouts, randomly chooses two of them, and returns them.
def choose_two(final_layouts, sums):
    selected = []
    for num in range(2):
        rand_num = random.random() * sum(sums)
        num_sum = 0
        i = -1
        while num_sum < rand_num:
            i = i + 1
            num_sum = num_sum + sums[i]
        selected.append(final_layouts[i])
    return selected[0], selected[1]


# Chooses random starting and ending indices, making sure that the start is less than or
# equal to the end. Generates a new layout, taking keys from outside the range from layout 1
# and keys from inside the range from the other.
def new_layout(layout1, layout2, removed_chars):
    final = []
    start = random.randint(0, len(layout1))
    end = random.randint(0, len(layout2))
    if start > end:
        start, end = end, start
    values = [x for x in layout1[start:end] if x not in removed_chars]
    layout2 = [x for x in layout2 if (x not in values and x not in removed_chars)]
    count1 = 0
    count2 = 0
    # Appends the values within the ranges to the final layout.
    for num in range(len(layout1)):
        if keys[num] in removed_chars:
            final.append(keys[num])
        elif num >= start and num < end:
            final.append(values[count1])
            count1 = count1 + 1
        else:
            final.append(layout2[count2])
            count2 = count2 + 1
    return final


# Uses a genetic algorithm to optimize the keyboard. If the generation is
# zero, randomly generates layouts and chooses the best fifteen. From that
# point on, uses a rank-based selection algorithm to choose and combine
# the best layouts, mutating to maintain a diverse population.
def genetic(string, sums, same_max_count, curr_max, gen, final_layouts, removed_chars):
    layouts = []
    # Tests if the generation is zero. If so, generates 100 new layouts.
    if gen == 0:
        for i in range(100):
            newBoard = copy.copy(keys)
            newBoard = shuffle_layout(newBoard, removed_chars)
            # Culls the list to the top fifteen.
            if (i < 15):
                final_layouts.append(newBoard)
                sums.append(layout_score(newBoard, string))
            else:
                key_sum = layout_score(newBoard, string)
                index = -1
                if min(sums) < key_sum:
                    index = sums.index(min(sums))
                if index != -1:
                    sums[index] = key_sum
                    final_layouts[index] = newBoard
        return sums, same_max_count, curr_max, final_layouts
    else:
        new_sums = []
        max_layout_score = max(sums)
        print("max: " + str(max_layout_score))
        layouts.append(final_layouts[sums.index(max_layout_score)])
        new_sums.append(max_layout_score)
        for j in range(100):
            layout1, layout2 = choose_two(final_layouts, sums)
            final = new_layout(layout1, layout2, removed_chars)
            if random.randint(0, 1) == 0:
                final = mutate(final, removed_chars)
            if len(layouts) < 15:
                layouts.append(final)
                new_sums.append(layout_score(final, string))
            else:
                final_sum = layout_score(final, string)
                if final_sum > min(new_sums):
                    minSum = min(new_sums)
                    ind = new_sums.index(minSum)
                    new_sums[ind] = final_sum
                    layouts[ind] = final
        # Sets the final layouts to the top ones, and randomly mutates.
        for j in range(15):
            final_layouts[j] = layouts[j]
            sums[j] = new_sums[j]
        # Checks if the current maximum sum is the same as the previous gen.
        if (curr_max == max(sums)):
            same_max_count += 1
        elif curr_max < max_layout_score:
            same_max_count = 1
            curr_max = max(sums)
        return new_sums, same_max_count, curr_max, final_layouts

def draw_image(layout):
    im = Image.new('RGBA', (600, 200), 'white')
    row_correction = [0, 10, 30]
    draw = ImageDraw.Draw(im)
    for letter in layout:
        letter_num = layout.index(letter)
        letter_row = rows[letter_num]
        corr = row_correction[letter_row]
        y = letter_row * 50
        index = rows.index(letter_row)
        new_fingers = fingers[index:]
        new_index = new_fingers.index(fingers[letter_num])
        while letter_num != index + new_index:
            new_index = new_index + 1
        x = 50 * new_index
        draw.rectangle((x + corr + 35, y + 25, x + corr + 85, y + 75), outline="black")
        draw.text((x + corr + 57, y + 45), letter, fill="black")
    im.save("static/layout.png")
    return im
