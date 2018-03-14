function ret = save_varying_betas(start_val, end_val, num_points)
    for n = 0:(num_points - 1)
        beta = start_val + n * (end_val - start_val) / num_points
        [x, y, Cp, Cl] = ktreff(0, 0.07, beta, 0.15, 1000)
        print_aerofoil_to_file(x, y, beta + "-beta-aerofoil.txt")
    end
end