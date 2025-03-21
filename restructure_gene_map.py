def modify_svg_content(content, old_pos_dict, new_pos_dict, text_pos_dict, GROUP1, GROUP2, GROUP3, GROUP4):
    for i in range(len(content)):
        if "font-size:" in content[i] and "px;" in content[i]:
            content[i] = ""

        if "r=\"20\"" in content[i]:
            content[i] = content[i].replace("r=\"20\"", "r=\"4\"")

        if "line class=\"nw_edge\"" in content[i] and ".0\" stroke=" in content[i]:
            content[i] = ""

        if "line class=\"nw_edge\"" in content[i] and ((".1\" stroke=" in content[i]) or (".2\" stroke=" in content[i])): #updating the edge pos
            old_width = float(content[i].split("stroke-width=\"")[1].split("\"")[0])
            old_opacity = float(content[i].split("stroke-opacity=\"")[1].split("\"")[0])
            new_width = str(0.45 * old_width)
            new_opacity = str(0.45 * old_opacity)

            old_x1 = content[i].split("x1=\"")[1].split("\"")[0]
            old_y1 = content[i].split("y1=\"")[1].split("\"")[0]
            old_x2 = content[i].split("x2=\"")[1].split("\"")[0]
            old_y2 = content[i].split("y2=\"")[1].split("\"")[0]

            mod_old_x1 = str(float(old_x1) - 0.5)
            mod_old_x2 = str(float(old_x2) - 0.5)
            mod_old_y1 = str(float(old_y1) - 0.5)
            mod_old_y2 = str(float(old_y2) - 0.5)

            if ".0" in mod_old_x1:
                mod_old_x1 = mod_old_x1[:-2]
            if ".0" in mod_old_x2:
                mod_old_x2 = mod_old_x2[:-2]
            if ".0" in mod_old_y1:
                mod_old_y1 = mod_old_y1[:-2]
            if ".0" in mod_old_y2:
                mod_old_y2 = mod_old_y2[:-2]

            gene1_name = old_pos_dict[str(mod_old_x1) + " " + str(mod_old_y1)]
            gene2_name = old_pos_dict[str(mod_old_x2) + " " + str(mod_old_y2)]

            if gene1_name in new_pos_dict and gene2_name in new_pos_dict:
                new_pos1 = new_pos_dict[gene1_name]
                new_pos2 = new_pos_dict[gene2_name]
                updated_new_pos1 = [str(float(new_pos1[0]) + 0.5), str(float(new_pos1[1]) + 0.5)]
                updated_new_pos2 = [str(float(new_pos2[0]) + 0.5), str(float(new_pos2[1]) + 0.5)]
                first_half = content[i].split("stroke-opacity=\"")[0]
                content[i] = first_half + "stroke-opacity=\"" + new_opacity + "\" stroke-width=\"" + new_width + "\" style=\"\""  +" x1=\"" + updated_new_pos1[0] + "\" y1=\"" + updated_new_pos1[1] + "\" x2=\"" + updated_new_pos2[0] + "\" y2=\"" + updated_new_pos2[1] + "\"/>\n"

        if "<circle cx" in content[i]:
            if "cx=\"" in content[i]:
                old_x = content[i].split("cx=\"")[1].split("\"")[0]
                old_y = content[i].split("cy=\"")[1].split("\"")[0]
                gene_name = old_pos_dict[str(old_x) + " " + str(old_y)]
                if gene_name in new_pos_dict:
                    new_pos = new_pos_dict[gene_name]
                    first_half = content[i].split(" cx=")[0]
                    second_half = content[i].split("fill=")[1]
                    content[i] = first_half + " cx=\"" + new_pos[0] + "\" cy=\"" + new_pos[1] + "\" fill=" + second_half

        if "<circle class" in content[i]:
            if "cx=\"" in content[i]:
                old_x = content[i].split("cx=\"")[1].split("\"")[0]
                old_y = content[i].split("cy=\"")[1].split("\"")[0]
                gene_name = old_pos_dict[str(old_x) + " " + str(old_y)]
                if gene_name in new_pos_dict:
                    new_pos = new_pos_dict[gene_name]
                    first_half = content[i].split(" cx=")[0]
                    second_half = content[i].split("display=")[1]
                    content[i] = first_half + " cx=\"" + new_pos[0] + "\" cy=\"" + new_pos[1] + "\" display=" + second_half

        if "<text " in content[i]:
            old_text_x = content[i].split(" x=\"")[1].split("\"")[0]
            old_text_y = content[i].split(" y=\"")[1].split("\"")[0]
            old_x = str(float(old_text_x) - 18)
            old_y = str(float(old_text_y) + 18)

            if ".0" in old_x:
                old_x = old_x[:-2]
            if ".0" in old_y:
                old_y = old_y[:-2]

            gene_name = old_pos_dict[str(old_x) + " " + str(old_y)]
            if gene_name in new_pos_dict:
                new_pos = new_pos_dict[gene_name]
                new_text_pos = text_pos_dict[gene_name]

                font_size = 17
                if gene_name in GROUP1:
                    font_size = 20
                elif gene_name in GROUP2:
                    font_size = 15
                elif gene_name in GROUP3:
                    font_size = 20
                elif gene_name in GROUP4:
                    font_size = 18

                first_half = content[i].split("x=")[0]
                first_half = first_half.replace("start", "middle") + "font-size=\"" + str(font_size) + "px\" "
                second_half = "x=\"" + new_text_pos[0] + "\" y=\"" + new_text_pos[1] + "\" alignment-baseline=\"central\">" + gene_name + "</text>\n"

                content[i] = first_half + second_half
    return content