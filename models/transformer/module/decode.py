import torch
from torch.autograd import Variable

from models.transformer.module.subsequent_mask import subsequent_mask


def decode(model, src, src_mask, max_len, type):
    ys = torch.ones(1)
    ys = ys.repeat(src.shape[0], 1).view(src.shape[0], 1).type_as(src.data)
    # ys shape [batch_size, 1]
    encoder_outputs = model.encode(src, src_mask)

    for i in range(max_len-1):
        out = model.decode(encoder_outputs, src_mask, Variable(ys),
                                  Variable(subsequent_mask(ys.size(1)).type_as(src.data)))

        log_prob = model.generator(out[:, -1])
        prob = torch.exp(log_prob)

        if type == 'greedy':
            _, next_word = torch.max(prob, dim = 1)
            ys = torch.cat([ys, next_word.unsqueeze(-1)], dim=1)  # [batch_size, i]
        elif type == 'multinomial':
            next_word = torch.multinomial(prob, 1)
            ys = torch.cat([ys, next_word], dim=1) #[batch_size, i]

    return ys

