struct Keccak256Hash:
    member word_1 : felt
    member word_2 : felt
    member word_3 : felt
    member word_4 : felt
end

# first 2 words are full
# the last word contains the remaining 4 bytes
struct Address:
    member word_1 : felt
    member word_2 : felt
    member word_3 : felt
end