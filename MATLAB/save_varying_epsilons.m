function ret = save_varying_epsilons(start_val, end_val, num_points)
    for n = 0:(num_points - 1)
        epsilon = start_val + n * (end_val - start_val) / num_points
        [x, y, Cp, Cl] = ktreff(0, epsilon, 0.02, 0.15, 2500)
        print_aerofoil_to_file(x, y, epsilon + "-epsilon-aerofoil.txt")
    end
end