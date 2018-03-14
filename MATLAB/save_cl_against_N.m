function ret = save_cl_against_N(min_panels, max_panels, step)
    file_id = fopen("dpan-results.txt", 'w');
    [~, ~, ~, Cl_ktreff] = ktreff(3.0 * pi / 180, 0.07, 0.02, 0.15, 160);
    fprintf(file_id, "ktreff,%f\n", Cl_ktreff);
    for n = min_panels:step:max_panels
        [x, y, ~, ~] = ktreff(0, 0.07, 0.02, 0.15, n);
        [~, Cl] = dpan(n, 3.0 * pi / 180.0, x, y);
        fprintf(file_id, "%i,%f\n", n, Cl);
    end
    fclose(file_id)
end