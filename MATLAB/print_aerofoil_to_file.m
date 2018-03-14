function ret = print_aerofoil_to_file(x, y, filename)
    file_id = fopen(filename, 'w');
    for i = 1:length(x)
         fprintf(file_id, '%f  %f\n', x(i), y(i));
    end
    fclose(file_id);
end
