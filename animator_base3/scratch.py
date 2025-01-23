def split_string(seg):
    # Find the position of the first '_{' and the last '}'
    start_idx = seg.find('_{')
    end_idx = seg.find('}', start_idx)
    
    if start_idx != -1 and end_idx != -1:
        # Extract the object part including the curly braces
        object_part = seg[start_idx:end_idx+1]
        
        # Remove the object part from the string
        seg = seg[:start_idx] + seg[end_idx+1:]
        
        # Remove the leading underscore from the object part
        object_part = object_part[1:]  # Strip the first character '_'
    else:
        object_part = ''  # If no object is found, set it to empty
    
    # Now split the remaining part by underscores
    parts = seg.split('_')
    
    # Add the object part as the last item
    if object_part:
        parts.append(object_part)
    
    return parts

# Example usage
input_string = "API_test-animation_{\"an\": \"L1100,L2100,L3100\"}"
print(split_string(input_string))

